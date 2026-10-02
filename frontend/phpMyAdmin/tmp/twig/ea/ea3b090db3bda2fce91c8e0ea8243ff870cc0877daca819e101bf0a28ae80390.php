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
class __TwigTemplate_5feed0804ac58a3457242208055234fbf5da08b69d98d2f9bb9c3cfafcbb5d12 extends \Twig\Template
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
        echo "<table class=\"pma-table\" id=\"initials_table\" cellspacing=\"5\">
    <tr>
        ";
        // line 3
        $context['_parent'] = $context;
        $context['_seq'] = twig_ensure_traversable(($context["array_initials"] ?? null));
        foreach ($context['_seq'] as $context["tmp_initial"] => $context["initial_was_found"]) {
            // line 4
            echo "          ";
            if ( !($context["tmp_initial"] === null)) {
                // line 5
                echo "            ";
                if ($context["initial_was_found"]) {
                    // line 6
                    echo "                <td>
                    <a class=\"ajax";
                    // line 8
                    echo (((array_key_exists("initial", $context) && (($context["initial"] ?? null) === $context["tmp_initial"]))) ? (" active") : (""));
                    // line 9
                    echo "\" href=\"";
                    echo PhpMyAdmin\Url::getFromRoute("/server/privileges", ["initial" => $context["tmp_initial"]]);
                    echo "\">";
                    // line 10
                    echo $context["tmp_initial"];
                    // line 11
                    echo "</a>
                </td>
            ";
                } else {
                    // line 14
                    echo "                <td>";
                    echo $context["tmp_initial"];
                    echo "</td>
            ";
                }
                // line 16
                echo "          ";
            }
            // line 17
            echo "        ";
        }
        $_parent = $context['_parent'];
        unset($context['_seq'], $context['_iterated'], $context['tmp_initial'], $context['initial_was_found'], $context['_parent'], $context['loop']);
        $context = array_intersect_key($context, $_parent) + $_parent;
        // line 18
        echo "        <td>
            <a href=\"";
        // line 19
        echo PhpMyAdmin\Url::getFromRoute("/server/privileges", ["showall" => 1]);
        echo "\" class=\"nowrap\">
                ";
        // line 20
        echo _gettext("Show all");
        // line 21
        echo "            </a>
        </td>
    </tr>
</table>
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
        return array (  91 => 21,  89 => 20,  85 => 19,  82 => 18,  76 => 17,  73 => 16,  67 => 14,  62 => 11,  60 => 10,  56 => 9,  54 => 8,  51 => 6,  48 => 5,  45 => 4,  41 => 3,  37 => 1,);
    }

    public function getSourceContext()
    {
        return new Source("", "server/privileges/initials_row.twig", "E:\\STUDENT\\phpMyAdmin\\templates\\server\\privileges\\initials_row.twig");
    }
}
