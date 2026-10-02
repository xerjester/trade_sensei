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

/* server/privileges/initials_row.twig */
class __TwigTemplate_5019037c1ef14f6558f91db7d1c50708cc066b4667277a44951a5e853251ff62 extends Template
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
        echo "<nav aria-label=\"";
echo _gettext("Pagination of user accounts");
        echo "\">
  <ul id=\"userAccountsPagination\" class=\"pagination\">
    ";
        // line 3
        $context['_parent'] = $context;
        $context['_seq'] = twig_ensure_traversable(($context["array_initials"] ?? null));
        foreach ($context['_seq'] as $context["tmp_initial"] => $context["initial_was_found"]) {
            // line 4
            echo "      ";
            if ( !($context["tmp_initial"] === null)) {
                // line 5
                echo "        ";
                if ($context["initial_was_found"]) {
                    // line 6
                    echo "          <li class=\"page-item";
                    echo (((($context["initial"] ?? null) === $context["tmp_initial"])) ? (" active") : (""));
                    echo "\"";
                    echo (((($context["initial"] ?? null) === $context["tmp_initial"])) ? (" aria-current=\"page\"") : (""));
                    echo ">
            <a class=\"page-link\" href=\"";
                    // line 7
                    echo PhpMyAdmin\Url::getFromRoute("/server/privileges", ["viewing_mode" => ($context["viewing_mode"] ?? null), "initial" => $context["tmp_initial"]]);
                    echo "\">";
                    echo twig_escape_filter($this->env, $context["tmp_initial"], "html", null, true);
                    echo "</a>
          </li>
        ";
                } else {
                    // line 10
                    echo "          <li class=\"page-item disabled\">
            <a class=\"page-link\" href=\"#\" tabindex=\"-1\" aria-disabled=\"true\">";
                    // line 11
                    echo twig_escape_filter($this->env, $context["tmp_initial"], "html", null, true);
                    echo "</a>
          </li>
        ";
                }
                // line 14
                echo "      ";
            }
            // line 15
            echo "    ";
        }
        $_parent = $context['_parent'];
        unset($context['_seq'], $context['_iterated'], $context['tmp_initial'], $context['initial_was_found'], $context['_parent'], $context['loop']);
        $context = array_intersect_key($context, $_parent) + $_parent;
        // line 16
        echo "    <li class=\"page-item\">
      <a class=\"page-link text-nowrap\" href=\"";
        // line 17
        echo PhpMyAdmin\Url::getFromRoute("/server/privileges", ["viewing_mode" => ($context["viewing_mode"] ?? null), "showall" => true]);
        echo "\">";
echo _gettext("Show all");
        echo "</a>
    </li>
  </ul>
</nav>
";
    }

    public function getTemplateName()
    {
        return "server/privileges/initials_row.twig";
    }

    public function isTraitable()
    {
        return false;
    }

    public function getDebugInfo()
    {
        return array (  89 => 17,  86 => 16,  80 => 15,  77 => 14,  71 => 11,  68 => 10,  60 => 7,  53 => 6,  50 => 5,  47 => 4,  43 => 3,  37 => 1,);
    }

    public function getSourceContext()
    {
        return new Source("", "server/privileges/initials_row.twig", "D:\\STUDENT\\phpMyAdmin\\templates\\server\\privileges\\initials_row.twig");
    }
}
