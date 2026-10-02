<?php

use Twig\Environment;
use Twig\Error\LoaderError;
use Twig\Error\RuntimeError;
use Twig\Extension\SandboxExtension;
use Twig\Markup;
use Twig\Sandbox\SecurityError;
use Twig\Sandbox\SecurityNotAllowedTagError;
use Twig\Sandbox\SecurityNotAllowedFilterError;
use Twig\Sandbox\SecurityNotAllowedFunctionError;
use Twig\Source;
use Twig\Template;

/* server/user_groups/user_groups.twig */
class __TwigTemplate_3a0336844cf9050894d0c710d6c50a837a3f0425f61f10b7fea5ba00c4904a1c extends \Twig\Template
{
    private $source;
    private $macros = [];

    public function __construct(Environment $env)
    {
        parent::__construct($env);

        $this->source = $this->getSourceContext();

        $this->parent = false;

        $this->blocks = [
        ];
    }

    protected function doDisplay(array $context, array $blocks = [])
    {
        $macros = $this->macros;
        // line 1
        echo "<div class=\"row\"><h2>";
        echo _gettext("User groups");
        echo "</h2></div>
";
        // line 2
        if ((($context["has_rows"] ?? null) > 0)) {
            // line 3
            echo "    <form name=\"userGroupsForm\" id=\"userGroupsForm\" action=\"";
            echo ($context["action"] ?? null);
            echo "\" method=\"post\">
        ";
            // line 4
            echo ($context["hidden_inputs"] ?? null);
            echo "
        <table class=\"table table-light table-striped table-hover\">
            <thead class=\"thead-light\">
                <tr class=\"text-nowrap\">
                    <th scope=\"col\">
                        ";
            // line 9
            echo _gettext("User groups");
            // line 10
            echo "                    </th>
                    <th scope=\"col\">
                        ";
            // line 12
            echo _gettext("Server level tabs");
            // line 13
            echo "                    </th>
                    <th scope=\"col\">
                        ";
            // line 15
            echo _gettext("Database level tabs");
            // line 16
            echo "                    </th>
                    <th scope=\"col\">
                        ";
            // line 18
            echo _gettext("Table level tabs");
            // line 19
            echo "                    </th>
                    <th scope=\"col\">
                        ";
            // line 21
            echo _gettext("Action");
            // line 22
            echo "                    </th>
                </tr>
            </thead>
            <tbody>
                ";
            // line 26
            $context['_parent'] = $context;
            $context['_seq'] = twig_ensure_traversable(($context["user_groups_values"] ?? null));
            foreach ($context['_seq'] as $context["_key"] => $context["groupName"]) {
                // line 27
                echo "                    <tr>
                        <td>";
                // line 28
                echo twig_escape_filter($this->env, twig_get_attribute($this->env, $this->source, $context["groupName"], "name", [], "any", false, false, false, 28), "html", null, true);
                echo "</td>
                        <td>";
                // line 29
                echo twig_escape_filter($this->env, twig_get_attribute($this->env, $this->source, $context["groupName"], "serverTab", [], "any", false, false, false, 29), "html", null, true);
                echo "</td>
                        <td>";
                // line 30
                echo twig_escape_filter($this->env, twig_get_attribute($this->env, $this->source, $context["groupName"], "dbTab", [], "any", false, false, false, 30), "html", null, true);
                echo "</td>
                        <td>";
                // line 31
                echo twig_escape_filter($this->env, twig_get_attribute($this->env, $this->source, $context["groupName"], "tableTab", [], "any", false, false, false, 31), "html", null, true);
                echo "</td>
                        <td class=\"text-nowrap\">
                            <a class=\"\" href=\"";
                // line 33
                echo twig_get_attribute($this->env, $this->source, $context["groupName"], "userGroupUrl", [], "any", false, false, false, 33);
                echo "\" data-post=\"";
                echo twig_get_attribute($this->env, $this->source, $context["groupName"], "viewUsersUrl", [], "any", false, false, false, 33);
                echo "\">";
                echo twig_get_attribute($this->env, $this->source, $context["groupName"], "viewUsersIcon", [], "any", false, false, false, 33);
                echo "</a>
                            &nbsp;&nbsp;
                            <a class=\"\" href=\"";
                // line 35
                echo twig_get_attribute($this->env, $this->source, $context["groupName"], "userGroupUrl", [], "any", false, false, false, 35);
                echo "\" data-post=\"";
                echo twig_get_attribute($this->env, $this->source, $context["groupName"], "editUsersUrl", [], "any", false, false, false, 35);
                echo "\">";
                echo twig_get_attribute($this->env, $this->source, $context["groupName"], "editUsersIcon", [], "any", false, false, false, 35);
                echo "</a>
                            &nbsp;&nbsp;
                            <a class=\"deleteUserGroup ajax\" href=\"";
                // line 37
                echo twig_get_attribute($this->env, $this->source, $context["groupName"], "userGroupUrl", [], "any", false, false, false, 37);
                echo "\" data-post=\"";
                echo twig_get_attribute($this->env, $this->source, $context["groupName"], "deleteUsersUrl", [], "any", false, false, false, 37);
                echo "\">";
                echo twig_get_attribute($this->env, $this->source, $context["groupName"], "deleteUsersIcon", [], "any", false, false, false, 37);
                echo "</a>
                        </td>
                    </tr>
                ";
            }
            $_parent = $context['_parent'];
            unset($context['_seq'], $context['_iterated'], $context['_key'], $context['groupName'], $context['_parent'], $context['loop']);
            $context = array_intersect_key($context, $_parent) + $_parent;
            // line 41
            echo "            </tbody>
        </table>
    </form>
";
        }
        // line 45
        echo "<div class=\"row\">
    <fieldset id=\"fieldset_add_user_group\">
        <a href=\"";
        // line 47
        echo ($context["add_user_url"] ?? null);
        echo "\">";
        echo ($context["add_user_icon"] ?? null);
        echo _gettext("Add user group");
        echo "</a>
    </fieldset>
</div>
";
    }

    public function getTemplateName()
    {
        return "server/user_groups/user_groups.twig";
    }

    public function isTraitable()
    {
        return false;
    }

    public function getDebugInfo()
    {
        return array (  155 => 47,  151 => 45,  145 => 41,  131 => 37,  122 => 35,  113 => 33,  108 => 31,  104 => 30,  100 => 29,  96 => 28,  93 => 27,  89 => 26,  83 => 22,  81 => 21,  77 => 19,  75 => 18,  71 => 16,  69 => 15,  65 => 13,  63 => 12,  59 => 10,  57 => 9,  49 => 4,  44 => 3,  42 => 2,  37 => 1,);
    }

    public function getSourceContext()
    {
        return new Source("", "server/user_groups/user_groups.twig", "E:\\STUDENT\\phpMyAdmin\\templates\\server\\user_groups\\user_groups.twig");
    }
}
